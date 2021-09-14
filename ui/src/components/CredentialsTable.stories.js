import CredentialsTable from "./CredentialsTable";

export default {
  title: "CredentialsTable",
  excludeStories: /.*Data$/
};

const template = `
  <credentials-table
    :fetch-credentials="fetchCredentials"
    :delete-credential="deleteCredential"
  />
`;

export const Default = () => ({
  components: { CredentialsTable },
  template: template,
  data() {
    return {
      response: {
        data: {
          credentials: {
            entities: [
              {
                createdAt: "2021-09-14T07:34:41.375401+00:00",
                name: "Personal access token",
                datasource: {
                  name: "GitHub"
                }
              },
              {
                createdAt: "2021-07-01T12:38:58.375401+00:00",
                name: "OAuth",
                datasource: {
                  name: "GitHub"
                }
              },
              {
                createdAt: "2020-01-08T09:45:00.375401+00:00",
                name: "Read-only token",
                datasource: {
                  name: "GitLab"
                }
              }
            ],
            pageInfo: {
              totalResults: 3,
              numPages: 1
            }
          }
        }
      }
    };
  },
  methods: {
    fetchCredentials() {
      return this.response;
    },
    deleteCredential() {
      return;
    }
  }
});

export const Empty = () => ({
  components: { CredentialsTable },
  template: template,
  data() {
    return {
      response: {
        data: {
          credentials: {
            entities: [],
            pageInfo: {
              totalResults: 0,
              numPages: 1
            }
          }
        }
      }
    };
  },
  methods: {
    fetchCredentials() {
      return this.response;
    },
    deleteCredential() {
      return;
    }
  }
});

import EcosystemTree from "./EcosystemTree.vue";

export default {
  title: "EcosystemTree",
  excludeStories: /.*Data$/
};

const ecosystemTreeTemplate = `
  <ecosystem-tree
    :ecosystem="ecosystem"
    :delete-project="mockAction"
    :move-project="mockAction"
    :delete-ecosystem="mockAction"
    :add-data-set="mockAction"
  />
`;

export const Default = () => ({
  components: { EcosystemTree },
  template: ecosystemTreeTemplate,
  data() {
    return {
      ecosystem: {
        id: 1,
        name: "ecosystem-name",
        title: "Ecosystem",
        projectSet: [
          {
            id: 1,
            name: "projectname",
            title: "Project 1",
            ecosystem: {
              name: "ecosystem-name"
            },
            parentProject: null,
            subprojects: [
              {
                id: 5,
                name: "subproject",
                title: "Subproject 1",
                ecosystem: {
                  name: "ecosystem-name"
                },
                parentProject: {
                  name: "projectname",
                  id: 1
                },
                subprojects: [
                  {
                    id: 6,
                    name: "sub-subproject",
                    title: "Sub-subproject title",
                    ecosystem: {
                      name: "ecosystem-name"
                    },
                    parentProject: {
                      name: "subproject",
                      id: 5
                    }
                  }
                ]
              },
              {
                id: 4,
                name: "subproject2",
                title: "Subproject 2",
                ecosystem: {
                  name: "ecosystem-name"
                },
                parentProject: {
                  name: "projectname",
                  id: 1
                }
              }
            ]
          },
          {
            id: 2,
            name: "projectname2",
            title: "Project 2",
            ecosystem: {
              name: "ecosystem-name"
            },
            parentProject: null
          },
          {
            id: 3,
            name: "projectname3",
            title: "Project 3",
            ecosystem: {
              name: "ecosystem-name"
            },
            parentProject: null
          }
        ]
      }
    };
  },
  methods: {
    mockAction() {
      return;
    }
  }
});

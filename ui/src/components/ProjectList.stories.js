import ProjectList from "./ProjectList.vue";

export default {
  title: "ProjectList",
  excludeStories: /.*Data$/
};

const ProjectListTemplate = `
  <project-list
    :projects="projects"
    ecosystemId="1"
    :parent-project="parentProject"
  />
`;

export const Default = () => ({
  components: { ProjectList },
  template: ProjectListTemplate,
  data() {
    return {
      projects: [
        {
          id: 2,
          name: "beast",
          title: "Beast",
          ecosystem: {
            id: 1
          },
          subprojects: [
            {
              id: 3,
              name: "dragon",
              title: "Dragon",
              ecosystem: {
                id: 1
              },
              subprojects: [
                {
                  id: 5,
                  name: "longhorn",
                  title: "Romanian Longhorn",
                  ecosystem: {
                    id: 1
                  },
                  subprojects: []
                }
              ]
            },
            {
              id: 6,
              name: "unicorn",
              title: "Unicorn",
              ecosystem: {
                id: 1
              },
              subprojects: []
            }
          ]
        },
        {
          id: 4,
          name: "goblin",
          title: "Goblin",
          ecosystem: {
            id: 1
          },
          subprojects: []
        }
      ],
      parentProject: {
        id: 1,
        name: "name"
      }
    };
  }
});

export const Empty = () => ({
  components: { ProjectList },
  template: ProjectListTemplate,
  data() {
    return {
      projects: [],
      parentProject: {
        id: 1,
        name: "name"
      }
    };
  }
});
